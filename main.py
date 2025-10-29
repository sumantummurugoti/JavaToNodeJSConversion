"""
Main Entry Point
Runs the Java to Node.js analyzer with modular LLM providers
"""

import os
import sys
from analyzer import JavaCodebaseAnalyzer
from llm_providers import create_provider, list_available_providers


def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("Java to Node.js Codebase Analyzer (Modular)")
    print("=" * 60)


def print_available_providers():
    """Display available LLM providers"""
    providers = list_available_providers()
    
    print("\nAvailable LLM Providers:")
    print("-" * 60)
    
    for provider_id, info in providers.items():
        status = "✓ Configured" if info["configured"] else "✗ Not configured"
        cost_badge = "FREE" if info["cost"] == "FREE" else "💳 Paid"
        
        print(f"\n{provider_id.upper():12} - {info['name']}")
        print(f"  Cost:      {cost_badge}")
        print(f"  Status:    {status}")
        
        if info["key_required"] and not info["configured"]:
            print(f"  Setup:     export {info['env_var']}='your-key'")
            print(f"  Get key:   {info['url']}")
        elif not info["configured"] and provider_id == "ollama":
            print(f"  Setup:     ollama serve")
            print(f"  Install:   {info['url']}")


def get_provider_choice() -> str:
    """Get provider choice from environment or user"""
    # Check environment variable
    provider = os.getenv("LLM_PROVIDER", "").lower()
    
    if provider in ["gemini", "openai", "anthropic", "ollama"]:
        return provider
    
    # Check which providers are configured
    providers = list_available_providers()
    configured = [p for p, info in providers.items() if info["configured"]]
    
    if configured:
        print(f"\n Found configured provider(s): {', '.join(configured)}")
        if "gemini" in configured:
            return "gemini"
        return configured[0]
    

    
    return None


def main():
    """Main execution function"""
    print_banner()
    print_available_providers()
    
    # Configuration
    GITHUB_URL = "https://github.com/janjakovacevic/SakilaProject.git"
    REPO_PATH = "./SakilaProject"
    
    # Get provider choice
    provider_name = get_provider_choice()
    
    if not provider_name:
        sys.exit(1)
    
    # Try different API keys
    api_key = (
        os.getenv("GEMINI_API_KEY") or
        os.getenv("OPENAI_API_KEY") or
        os.getenv("ANTHROPIC_API_KEY")
    )
    
    # Initialize provider
    print("\n" + "=" * 60)
    try:
        provider = create_provider(provider_name, api_key)
    except ValueError as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
    
    # Initialize analyzer
    analyzer = JavaCodebaseAnalyzer(REPO_PATH, provider)
    
    # Clone repository if needed
    if not os.path.exists(REPO_PATH):
        print(f"\n Cloning repository...")
        try:
            analyzer.clone_repository(GITHUB_URL)
        except Exception as e:
            print(f" Failed to clone: {e}")
            sys.exit(1)
    
    # Analyze codebase
    print("\n" + "=" * 60)
    try:
        analyzer.analyze_codebase()
    except Exception as e:
        print(f"\n Analysis failed: {e}")
        sys.exit(1)
    
    # Export knowledge
    print("\n" + "=" * 60)
    analyzer.export_knowledge()
    
    # Convert selected files
    print("\n" + "=" * 60)
    print(" Converting to Node.js...")
    selected = analyzer.select_files_for_conversion()
    
    for module_type, module in selected.items():
        print(f"\n  Converting {module_type}: {module.name}")
        try:
            analyzer.convert_to_nodejs(module)
        except Exception as e:
            print(f"  ✗ Conversion failed: {e}")
    
    print("\n" + "=" * 60)
    print(" Analysis and conversion complete!")
    print("=" * 60)
    print("\n Output files:")
    print("  - codebase_analysis.json  (Structured analysis)")
    print("  - converted/*.js          (Node.js files)")
    print("\n Next steps:")
    print("  1. Review: cat codebase_analysis.json | jq")
    print("  2. Setup:  cd converted && npm install")
    print("  3. Run:    npm start")
    print("")


if __name__ == "__main__":
    main()
