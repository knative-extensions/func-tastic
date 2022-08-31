# Node.js Metacontroller for Functions

This function uses the Metacontroller API to provide a controller which
creates a Knative `Trigger` instance for each additional function deployed
to the namespace. This project can be used as a template for Knative
Functions using the `--repository` flag. You can use this template to create
a more robust, feature-full function. More on that later.

## Prerequisites

To use this function to manage your Knative Functions, you'll need to have a
few things already installed on your cluster.

- Knative Serving and Eventing: https://knative.dev/docs/install/
- Metacontroller API: https://metacontroller.github.io/metacontroller/guide/install.html

For your local developer experience, you'll need the following CLI tooling.

- The `kn` CLI: https://github.com/knative/client
- The `kubectl` CLI: https://kubernetes.io/docs/tasks/tools/#kubectl
- The `func` CLI: https://github.com/knative-sandbox/kn-plugin-func

Finally, you'll want to have a default broker available, and a `PingSource` to ensure that
the `Triggers` are correctly created.

```
❯ kn broker create default
❯ kn source ping create pinger --schedule "*/1 * * * *" --data '{ "message": "Hello" }' --sink broker:default
```

## Installing

Once you have all of the prerequisites installed, you can install this metacontroller
function using the `func` CLI.

- Create the function locally and then deploy it.

```
func create -l nodejs -t metacontroller --repository https://github.com/knative-sandbox/func-tastic metacontroller
func deploy -p metacontroller
```

Check that everything is OK.

```
❯ func list
NAME            NAMESPACE  RUNTIME  URL                                               READY
metacontroller  default    node     http://metacontroller.default.127.0.0.1.sslip.io  True
```

Now deploy a function which the metacontroller will create a trigger for.

```
❯ func create -l node -t cloudevent viewer
# Modify the function to simply return 'OK'
❯ func deploy
```

You should now see a new trigger created.

```
❯ kn triggers list
NAME                            BROKER    SINK          AGE     CONDITIONS   READY   REASON
viewer-default-broker-trigger   default   ksvc:viewer   4h16m   6 OK / 6     True
```

To check whether the function is now receiving events from the broker, check the logs.

```
❯ k get pods
NAME                                       READY   STATUS    RESTARTS   AGE
viewer-00009-deployment-5ff8bb9744-c9m6c   2/2     Running   0          4m29s
❯ k logs -f viewer-00009-deployment-5ff8bb9744-c9m6c user-container
{"level":40,"time":1661196180153,"pid":1,"hostname":"viewer-00009-deployment-5ff8bb9744-c9m6c","reqId":"req-5","msg":"{ \"message\": \"Hello\" }"}
{"level":40,"time":1661196180157,"pid":1,"hostname":"viewer-00009-deployment-5ff8bb9744-c9m6c","reqId":"req-5","msg":"dev.knative.sources.ping"}
```

## Next steps

Typically functions will not want to receive all events from the broker. See if you can modify the metacontroller
source to check for function provided metadata (labels, annotations or environment variables), and if found use
that to create event filters on the returned `Trigger`.
