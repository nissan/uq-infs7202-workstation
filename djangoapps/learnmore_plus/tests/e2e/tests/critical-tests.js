// @ts-check
const { test: baseTest } = require('@playwright/test');

/**
 * Define a test with the @critical tag
 * This will allow us to run only critical tests with --grep="@critical"
 */
exports.test = baseTest.extend({
  // Add any specific setup for critical tests here
})('Critical Tests @critical');

/**
 * Create shorthand export of the same test object for use in test files
 */
module.exports = {
  test: exports.test,
  expect: baseTest.expect,
};