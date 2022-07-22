
const handle = async (context) => {
  const service = context.body.object

  // Skip updating the controller itself
  if (!!service?.metadata?.labels["function-controller"]) {
    console.warn("Not updating the controller")
    return {}
  }

  // Create a Trigger for this function on the default broker
  const attachments = [
    {
      apiVersion: "eventing.knative.dev/v1",
      kind: "Trigger",
      metadata: {
        name: service.metadata.name + "-default-broker-trigger"
      },
      spec: {
        broker: "default",
        subscriber: {
          ref: {
            apiVersion: "serving.knative.dev/v1",
            kind: "Service",
            name: service.metadata.name
          }
        }
      }
    }
  ];

  return { attachments };
}

// Export the function
module.exports = { handle };
