'use strict';

/**
 * stop-time service.
 */

const { createCoreService } = require('@strapi/strapi').factories;

module.exports = createCoreService('api::stop-time.stop-time');
