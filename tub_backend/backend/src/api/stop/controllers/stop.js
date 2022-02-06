'use strict';

/**
 *  stop controller
 */

const { createCoreController } = require('@strapi/strapi').factories;

module.exports = createCoreController('api::stop.stop');
