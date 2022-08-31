'use strict';

const func = require('..').handle;
const test = require('tape');

// A Knative Service managed by the controller
const service = {
  metadata:
  {
    name: "my-function",
    labels:
      { "service.knative.dev": true }
  }
}

// The Knative Service representing the controller itself
const controller = {
  metadata:
  {
    name: "function-controller",
    labels: {
      ...service.metadata.labels,
      "function-controller": true,
    },
  }
}

test('Unit: returns an empty object when invoked with itself', async t => {
  t.plan(1);
  // Invoke the function, which should complete without error.
  const result = await func({ body: { object: controller } });
  t.deepEqual(result, {});
  t.end();
});

test('Unit: returns a list of one Knative Trigger when invoked with a Service', async t => {
  t.plan(2);
  // Invoke the function, which should complete without error.
  const result = await func({ body: { object: service } });
  t.equal(result.attachments.length, 1);
  t.equal(result.attachments[0].kind, "Trigger")
  t.end();
});

test('Unit: returns a Knative Trigger named <servicename>-default-broker-trigger', async t => {
  t.plan(2);
  // Invoke the function, which should complete without error.
  const result = await func({ body: { object: service } });
  t.equal(result.attachments.length, 1);
  t.equal(result.attachments[0].metadata.name, service.metadata.name + "-default-broker-trigger")
  t.end();
});

