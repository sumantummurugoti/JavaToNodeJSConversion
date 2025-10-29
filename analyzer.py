"""
Java Codebase Analyzer
Main analyzer class with Node.js conversion
"""

import os
import json
import re
import time
from pathlib import Path
from typing import Dict, List
from models import MethodInfo, ModuleInfo
from llm_providers import LLMProvider


class JavaCodebaseAnalyzer:
    """Analyzes Java codebase and converts to Node.js"""
    
    def __init__(self, repo_path: str, provider: LLMProvider):
        self.repo_path = Path(repo_path)
        self.provider = provider
        self.modules: List[ModuleInfo] = []
        self.project_overview = ""
        print(f"Using LLM provider: {provider.get_provider_name()}")
    
    def clone_repository(self, github_url: str):
        """Clone the GitHub repository locally"""
        import subprocess
        try:
            subprocess.run(
                ["git", "clone", github_url, str(self.repo_path)],
                check=True,
                capture_output=True
            )
            print(f"Repository cloned to {self.repo_path}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone repository: {e}")
            raise
    
    def find_java_files(self) -> List[Path]:
        """Recursively find all Java files in the codebase"""
        java_files = []
        for path in self.repo_path.rglob("*.java"):
            if "test" not in str(path).lower():
                java_files.append(path)
        return java_files
    
    def categorize_file(self, file_path: Path) -> str:
        """Categorize Java file based on naming conventions and content"""
        file_name = file_path.stem
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = ''.join([next(f, '') for _ in range(50)])
        except:
            content = ""
        
        if "Controller" in file_name or "@Controller" in content or "@RestController" in content:
            return "Controller"
        elif "Service" in file_name or "@Service" in content:
            return "Service"
        elif "Repository" in file_name or "DAO" in file_name or "@Repository" in content:
            return "DAO"
        elif "Entity" in file_name or "@Entity" in content:
            return "Model"
        elif "Config" in file_name or "@Configuration" in content:
            return "Configuration"
        elif "Application" in file_name:
            return "Application"
        else:
            return "Utility"
    
    def read_file_content(self, file_path: Path) -> str:
        """Read and return file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""
    
    def chunk_code(self, code: str, max_tokens: int = 3000) -> List[str]:
        """Smart chunking that respects code structure"""
        max_chars = max_tokens * 4
        chunks = []
        
        # Split by class boundaries
        class_pattern = r'((?:public|private|protected)?\s*(?:static)?\s*class\s+\w+[^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\})'
        classes = re.findall(class_pattern, code, re.DOTALL)
        
        if classes:
            for cls in classes:
                if len(cls) <= max_chars:
                    chunks.append(cls)
                else:
                    method_chunks = self._chunk_by_methods(cls, max_chars)
                    chunks.extend(method_chunks)
        else:
            for i in range(0, len(code), max_chars):
                chunks.append(code[i:i + max_chars])
        
        return chunks if chunks else [code[:max_chars]]
    
    def _chunk_by_methods(self, code: str, max_chars: int) -> List[str]:
        """Split large class by method boundaries"""
        chunks = []
        
        class_header_match = re.match(r'(.*?)((?:public|private|protected)\s+\w+\s+\w+\s*\([^)]*\))', code, re.DOTALL)
        class_header = class_header_match.group(1) if class_header_match else ""
        
        method_pattern = r'((?:public|private|protected)\s+(?:static\s+)?[\w<>\[\]]+\s+\w+\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{)'
        method_starts = [(m.start(), m.group(0)) for m in re.finditer(method_pattern, code)]
        
        if not method_starts:
            for i in range(0, len(code), max_chars):
                chunks.append(code[i:i + max_chars])
            return chunks
        
        methods = []
        for i, (start, signature) in enumerate(method_starts):
            end = method_starts[i + 1][0] if i + 1 < len(method_starts) else len(code)
            method_body = code[start:end]
            methods.append((signature, method_body))
        
        current_chunk = class_header
        for signature, method_body in methods:
            if len(current_chunk) + len(method_body) <= max_chars:
                current_chunk += method_body
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk)
                current_chunk = class_header + method_body
        
        if current_chunk.strip():
            chunks.append(current_chunk)
        
        return chunks
    
    def extract_dependencies(self, code: str) -> List[str]:
        """Extract import statements to identify dependencies"""
        imports = re.findall(r'import\s+([\w\.]+);', code)
        dependencies = [imp for imp in imports if 'sakilaproject' in imp.lower()]
        return list(set(dependencies))
    
    def call_llm(self, prompt: str) -> str:
        """Call the configured LLM provider"""
        try:
            return self.provider.analyze_code(prompt)
        except Exception as e:
            print(f"LLM call failed: {e}")
            return self._fallback_analysis(prompt)
    
    def _fallback_analysis(self, code_context: str) -> str:
        """Simple regex-based analysis when LLM fails"""
        methods = re.findall(r'public\s+\w+\s+(\w+)\s*\([^)]*\)', code_context)
        return json.dumps({
            "description": "Automated analysis (LLM unavailable)",
            "methods": [
                {
                    "name": m,
                    "signature": f"public void {m}()",
                    "description": "Method extracted via regex",
                    "complexity": "Medium"
                } for m in methods[:5]
            ]
        })
    
    def analyze_file(self, file_path: Path) -> ModuleInfo:
        """Analyze a single Java file and extract metadata"""
        content = self.read_file_content(file_path)
        file_type = self.categorize_file(file_path)
        dependencies = self.extract_dependencies(content)
        
        chunks = self.chunk_code(content, max_tokens=3000)
        all_methods = []
        description = ""
        
        for chunk_idx, chunk in enumerate(chunks):
            if len(chunks) > 1:
                print(f"    Processing chunk {chunk_idx + 1}/{len(chunks)}...")
            
            prompt = f"""Analyze this Java {file_type} class and provide structured information.
Return ONLY valid JSON with this exact structure (no markdown, no explanation):
{{
  "description": "Brief description of the class purpose",
  "methods": [
    {{
      "name": "methodName",
      "signature": "public ReturnType methodName(params)",
      "description": "What the method does",
      "complexity": "Low|Medium|High"
    }}
  ]
}}

Java code (chunk {chunk_idx + 1} of {len(chunks)}):
{chunk}
"""
            
            response = self.call_llm(prompt)
            
            try:
                response = response.replace("```json", "").replace("```", "").strip()
                analysis = json.loads(response)
                
                if chunk_idx == 0 and analysis.get("description"):
                    description = analysis.get("description", "")
                
                for method in analysis.get("methods", []):
                    all_methods.append(MethodInfo(
                        name=method.get("name", "unknown"),
                        signature=method.get("signature", ""),
                        description=method.get("description", ""),
                        complexity=method.get("complexity", "Medium")
                    ))
            except json.JSONDecodeError:
                if chunk_idx == 0:
                    description = "Analysis unavailable"
        
        return ModuleInfo(
            name=file_path.stem,
            type=file_type,
            description=description,
            file_path=str(file_path.relative_to(self.repo_path)),
            methods=all_methods,
            dependencies=dependencies
        )
    
    def analyze_codebase(self):
        """Analyze entire codebase"""
        print("Scanning Java files...")
        java_files = self.find_java_files()
        print(f"Found {len(java_files)} Java files")
        
        print("\n Analyzing files...")
        for i, file_path in enumerate(java_files, 1):
            print(f"  [{i}/{len(java_files)}] {file_path.name}")
            time.sleep(2)  # To avoid rate limits
            module = self.analyze_file(file_path)
            self.modules.append(module)
        
        self._generate_project_overview()
    
    def _generate_project_overview(self):
        """Generate high-level project overview"""
        prompt = f"""Based on this Java project structure, provide a concise overview (2-3 sentences):

Project has {len(self.modules)} modules:
- {sum(1 for m in self.modules if m.type == 'Controller')} Controllers
- {sum(1 for m in self.modules if m.type == 'Service')} Services
- {sum(1 for m in self.modules if m.type == 'DAO')} DAOs
- {sum(1 for m in self.modules if m.type == 'Model')} Models

Module names: {', '.join([m.name for m in self.modules[:10]])}
"""
        
        response = self.call_llm(prompt)
        self.project_overview = response.strip()
    
    def export_knowledge(self, output_path: str = "codebase_analysis.json"):
        """Export structured knowledge to JSON"""
        data = {
            "projectOverview": self.project_overview,
            "modules": [m.to_dict() for m in self.modules],
            "statistics": {
                "totalModules": len(self.modules),
                "byType": {
                    module_type: sum(1 for m in self.modules if m.type == module_type)
                    for module_type in set(m.type for m in self.modules)
                }
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n✓ Knowledge exported to {output_path}")
    
    def select_files_for_conversion(self) -> Dict[str, ModuleInfo]:
        """Select one Controller, Service, and DAO for conversion"""
        #Select one controller, service and dao for conversion
        # selected = {}
        
        # for module_type in ['Controller', 'Service', 'DAO']:
        #     candidates = [m for m in self.modules if m.type == module_type]
        #     if candidates:
        #         selected[module_type] = candidates[0]
        
        # return selected
        
        time.sleep(2)
        selected = {}

        #Match the controller, service and DAO names
        # Step 1: Select the first Controller
        controller_candidates = [m for m in self.modules if m.type == 'Controller']
        if controller_candidates:
            selected['Controller'] = controller_candidates[0]
            controller_name = controller_candidates[0].name
            # Strip suffix like 'Controller' to get base name
            base_name = controller_name.replace('Controller', '')
        else:
            base_name = None

        # Step 2: Match Service and DAO using base name
        for module_type in ['Service', 'DAO']:
            candidates = [m for m in self.modules if m.type == module_type]
            time.sleep(2)
            if candidates:
                if base_name:
                    # Match if name starts with base_name (e.g. ActorService)
                    match = next((m for m in candidates if m.name.startswith(base_name)), None)
                    selected[module_type] = match if match else candidates[0]
                else:
                    selected[module_type] = candidates[0]

        return selected
    
    def convert_to_nodejs(self, java_module: ModuleInfo, output_dir: str = "converted"):
        """Convert Java class to Node.js equivalent - IMPROVED VERSION"""
        java_code = self.read_file_content(self.repo_path / java_module.file_path)
        
        # Determine appropriate chunk size based on module type
        chunk_size = 2000 if java_module.type == "Controller" else 2500
        chunks = self.chunk_code(java_code, max_tokens=chunk_size)
        nodejs_code_parts = []
        print(f"    before foreach loop chunk_size: {chunk_size}")
        print(f"    before foreach loop chunks length: {len(chunks)}")

        for chunk_idx, chunk in enumerate(chunks):
            if len(chunks) > 1:
                print(f"    Converting chunk {chunk_idx + 1}/{len(chunks)}...")
            
            # IMPROVED CONVERSION PROMPT
            conversion_prompt = self._create_conversion_prompt(java_module, chunk, chunk_idx, len(chunks))
            
            nodejs_code = self.call_llm(conversion_prompt)
            nodejs_code = self._clean_llm_response(nodejs_code)
            nodejs_code_parts.append(nodejs_code)
        
        # Combine chunks if multiple
        if len(chunks) > 1:
            final_code = self._merge_converted_chunks(nodejs_code_parts, java_module.type)
        else:
            final_code = nodejs_code_parts[0]
        
        # Clean up the converted code
        final_code = self._cleanup_converted_code(final_code, java_module)
        
        # Save to appropriate directory with proper naming
        output_file = self._save_converted_file(final_code, java_module, output_dir)
        
        print(f"Converted {java_module.name} → {output_file}")
        return output_file
    
    def _create_conversion_prompt(self, module: ModuleInfo, chunk: str, chunk_idx: int, total_chunks: int) -> str:
        """Create an improved conversion prompt with strict rules"""
        
        module_type = module.type
        
        base_instructions = """
CRITICAL RULES - MUST FOLLOW:
1. Generate code for EXACTLY ONE file - this {module_type} ONLY
2. Use CommonJS: const x = require('...') and module.exports
3. Use placeholder requires for dependencies (do NOT generate those files)
4. DO NOT include multiple modules in one file
5. DO NOT add example usage, test code, or extra files
6. DO NOT use ES6 imports (no import/export statements)
7. Start with require statements, end with module.exports, nothing else

OUTPUT STRUCTURE:
- Require statements at top
- Main code (functions/routes/logic)
- module.exports at bottom
- NO markdown, NO explanations, NO other files
"""
        
        if module.type == "Controller":
            specific_instructions = """
For Controllers (REST endpoints):
- Use: const express = require('express'); const router = express.Router();
- Define routes with: router.get('/path', async (req, res) => {...})
- Include error handling in each route
- End with: module.exports = router;
- Reference service as: const service = require('../services/ServiceName');
"""
        elif module.type == "Service":
            specific_instructions = """
For Services (business logic):
- Define async functions for each operation
- Use: const repository = require('../repositories/RepositoryName');
- Include try-catch for error handling
- End with: module.exports = { functionName1, functionName2, ... };
"""
        elif module.type == "DAO":
            specific_instructions = """
For DAOs/Repositories (data access):
- Use: const Model = require('../models/ModelName');
- Define async functions for CRUD operations
- Use Sequelize methods: findByPk, findAll, findOne, create, update, destroy
- End with: module.exports = { functionName1, functionName2, ... };
"""
        else:
            specific_instructions = ""
        
        chunk_context = ""
        if total_chunks > 1:
            chunk_context = f"\nThis is chunk {chunk_idx + 1} of {total_chunks}. Focus on converting this portion cleanly."
        
        prompt = f"""{base_instructions}

{specific_instructions}

JAVA {module.type.upper()} TO CONVERT:{chunk_context}

{chunk}

Generate clean, compilable Node.js code for THIS {module.type} ONLY. No other files."""
        
        return prompt
        #return prompt.format(module_type=module.type)
    
    def _clean_llm_response(self, response: str) -> str:
        """Clean up LLM response to extract just the code"""
        # Remove markdown code fences
        response = response.replace("```javascript", "").replace("```js", "").replace("```", "")
        
        # Remove any explanatory text before the code
        lines = response.split('\n')
        code_started = False
        cleaned_lines = []
        
        for line in lines:
            # Detect start of actual code
            if not code_started and (
                line.strip().startswith('const ') or
                line.strip().startswith('/**') or
                line.strip().startswith('//') or
                line.strip().startswith('module.exports')
            ):
                code_started = True
            
            if code_started:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def _cleanup_converted_code(self, code: str, module: ModuleInfo) -> str:
        """Clean up and validate the converted code"""
        
        # Remove any duplicate require statements
        lines = code.split('\n')
        seen_requires = set()
        cleaned_lines = []
        
        for line in lines:
            if line.strip().startswith('const ') and 'require(' in line:
                if line not in seen_requires:
                    seen_requires.add(line)
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
        
        code = '\n'.join(cleaned_lines)
        
        # Ensure proper module.exports
        if 'module.exports' not in code:
            code = self._add_module_exports(code, module)
        
        # Add file header comment
        header = f'''/**
 * {module.name}
 * Converted from Java {module.type} to Node.js
 * Type: {module.type}
 */

'''
        
        if not code.startswith('/**'):
            code = header + code
        
        return code
    
    def _add_module_exports(self, code: str, module: ModuleInfo) -> str:
        """Add appropriate module.exports based on module type"""
        
        if module.type == "Controller":
            if 'const router' in code:
                return code + '\n\nmodule.exports = router;\n'
        
        # Extract function names for Service/DAO
        func_pattern = r'(?:async\s+)?function\s+(\w+)\s*\('
        functions = re.findall(func_pattern, code)
        
        if functions:
            exports = ',\n    '.join(functions)
            return code + f'\n\nmodule.exports = {{\n    {exports}\n}};\n'
        
        return code
    
    def _save_converted_file(self, code: str, module: ModuleInfo, output_dir: str) -> str:
        """Save converted file to appropriate directory with proper naming"""
        
        # Create directory structure
        os.makedirs(output_dir, exist_ok=True)
        
        # Determine output path based on module type
        if module.type == "Controller":
            subdir = os.path.join(output_dir, "routes")
            os.makedirs(subdir, exist_ok=True)
            file_name = module.name.replace('Controller', '').lower() + '.route.js'
            output_file = os.path.join(subdir, file_name)
        
        elif module.type == "Service":
            subdir = os.path.join(output_dir, "services")
            os.makedirs(subdir, exist_ok=True)
            file_name = module.name + '.js'
            output_file = os.path.join(subdir, file_name)
        
        elif module.type == "DAO":
            subdir = os.path.join(output_dir, "repositories")
            os.makedirs(subdir, exist_ok=True)
            file_name = module.name.replace('Repository', '').replace('DAO', '').lower() + '.repository.js'
            output_file = os.path.join(subdir, file_name)
        
        elif module.type == "Model":
            subdir = os.path.join(output_dir, "models")
            os.makedirs(subdir, exist_ok=True)
            file_name = module.name + '.js'
            output_file = os.path.join(subdir, file_name)
        
        else:
            output_file = os.path.join(output_dir, module.name + '.js')
        
        # Write the file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        return output_file
    
    def _merge_converted_chunks(self, code_parts: List[str], module_type: str) -> str:
        """Intelligently merge multiple converted code chunks"""
        if not code_parts:
            return ""
        
        if len(code_parts) == 1:
            return code_parts[0]
        
        # Collect all unique requires and imports
        all_requires = set()
        all_body_lines = []
        
        for part in code_parts:
            lines = part.split('\n')
            body_lines = []
            
            for line in lines:
                # Extract require statements
                if line.strip().startswith('const ') and 'require(' in line:
                    all_requires.add(line)
                # Skip module.exports (will add at end)
                elif not line.strip().startswith('module.exports'):
                    body_lines.append(line)
            
            all_body_lines.extend(body_lines)
        
        # Reconstruct file
        result = []
        
        # Add requires at top
        if all_requires:
            result.extend(sorted(all_requires))
            result.append('')
        
        # Add body
        result.extend(all_body_lines)
        
        return '\n'.join(result)