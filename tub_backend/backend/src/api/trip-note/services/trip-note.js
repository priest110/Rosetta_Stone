'use strict';

/**
 * trip-note service.
 */

const { createCoreService } = require('@strapi/strapi').factories;

module.exports = createCoreService('api::trip-note.trip-note');
