/**
 * ActorController
 * Converted from Java Controller to Node.js
 * Type: Controller
 */

const express = require('express');
const router = express.Router();

const filmService = require('../services/FilmService');
const actorService = require('../services/ActorService');

router.get('/actors', async (req, res) => {
    try {
        const firstNameFilter = req.query.firstName || "ALL ACTORS";
        const lastNameFilter = req.query.lastName || "ALL ACTORS";
        let actors;

        if (firstNameFilter === "ALL ACTORS" && lastNameFilter === "ALL ACTORS") {
            actors = await actorService.getAllActors();
        } else if (lastNameFilter === "ALL ACTORS") {
            actors = await actorService.getActorsByFirstName(firstNameFilter);
        } else if (firstNameFilter === "ALL ACTORS") {
            actors = await actorService.getActorsByLastName(lastNameFilter);
        } else {
            actors = await actorService.getActorsByFullName(firstNameFilter, lastNameFilter);
        }

        const allActors = await actorService.getAllActors();

        res.json({
            actors: actors,
            allActors: allActors
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Error fetching actors' });
    }
});

router.get('/actors/details', async (req, res) => {
    try {
        const id = parseInt(req.query.id);

        if (isNaN(id)) {
            return res.status(400).json({ message: 'Invalid actor ID' });
        }

        const name = await actorService.getActorFullNameFromID(id);
        const films = await filmService.getFilmsByActor(id);

        res.json({
            name: name,
            films: films
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Error fetching actor details' });
    }
});

async function findActorById(id) {
    try {
        return await actorService.getActorByID(id);
    } catch (error) {
        console.error(error);
        return null;
    }
}

async function getActorFullNameFromID(id) {
    try {
        const actor = await actorService.getActorByID(id);
        return actor.firstName + " " + actor.lastName;
    } catch (error) {
        console.error(error);
        return null;
    }
}

module.exports = router;