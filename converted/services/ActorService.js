/**
 * ActorService
 * Converted from Java Service to Node.js
 * Type: Service
 */

const actorRepository = require('../repositories/ActorRepository');

const getAllActors = async () => {
    try {
        return await actorRepository.findAll();
    } catch (error) {
        console.error("Error getting all actors:", error);
        throw error;
    }
};

const getActorByID = async (id) => {
    try {
        return await actorRepository.getActorByActorId(id);
    } catch (error) {
        console.error(`Error getting actor by ID ${id}:`, error);
        throw error;
    }
};

const getActorsByFullName = async (firstName, lastName) => {
    try {
        return await actorRepository.findActorsByFirstNameAndLastName(firstName, lastName);
    } catch (error) {
        console.error(`Error getting actors by full name ${firstName} ${lastName}:`, error);
        throw error;
    }
};

const getActorsByFirstName = async (firstName) => {
    try {
        return await actorRepository.findActorsByFirstName(firstName);
    } catch (error) {
        console.error(`Error getting actors by first name ${firstName}:`, error);
        throw error;
    }
};

const getActorsByLastName = async (lastName) => {
    try {
        return await actorRepository.findActorsByLastName(lastName);
    } catch (error) {
        console.error(`Error getting actors by last name ${lastName}:`, error);
        throw error;
    }
};

const getActorFullNameFromID = async (id) => {
    try {
        const actor = await getActorByID(id);
        if (!actor) {
            return null;
        }
        return actor.firstName + " " + actor.lastName;
    } catch (error) {
        console.error(`Error getting actor full name from ID ${id}:`, error);
        throw error;
    }
};

module.exports = {
    getAllActors,
    getActorByID,
    getActorsByFullName,
    getActorsByFirstName,
    getActorsByLastName,
    getActorFullNameFromID
};