'use strict';

/**
 * stop router.
 */

const { createCoreRouter } = require('@strapi/strapi').factories;

module.exports = createCoreRouter('api::stop.stop');
