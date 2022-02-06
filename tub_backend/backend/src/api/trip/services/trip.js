'use strict';

/**
 * trip service.
 */

const { createCoreService } = require('@strapi/strapi').factories;

module.exports = createCoreService('api::trip.trip');
