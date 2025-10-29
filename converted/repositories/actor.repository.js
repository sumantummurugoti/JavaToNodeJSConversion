/**
 * ActorRepository
 * Converted from Java DAO to Node.js
 * Type: DAO
 */

const Actor = require('../models/Actor');

const findActorsByFirstNameAndLastName = async (firstName, lastName) => {
  try {
    const actors = await Actor.findAll({
      where: {
        firstName: firstName,
        lastName: lastName
      }
    });
    return actors;
  } catch (error) {
    console.error('Error finding actors:', error);
    throw error;
  }
};

const findActorsByFirstName = async (firstName) => {
  try {
    const actors = await Actor.findAll({
      where: {
        firstName: firstName
      }
    });
    return actors;
  } catch (error) {
    console.error('Error finding actors:', error);
    throw error;
  }
};

const findActorsByLastName = async (lastName) => {
  try {
    const actors = await Actor.findAll({
      where: {
        lastName: lastName
      }
    });
    return actors;
  } catch (error) {
    console.error('Error finding actors:', error);
    throw error;
  }
};

const getActorByActorId = async (id) => {
  try {
    const actor = await Actor.findByPk(id);
    return actor;
  } catch (error) {
    console.error('Error finding actor:', error);
    throw error;
  }
};

module.exports = {
  findActorsByFirstNameAndLastName,
  findActorsByFirstName,
  findActorsByLastName,
  getActorByActorId
};