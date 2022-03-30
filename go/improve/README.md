# Go Cloud Events Function

Welcome to your new Go Function! The boilerplate function code can be found in [`handle.go`](handle.go). This Function is meant to respond exclusively to [Cloud Events](https://cloudevents.io/), but you can remove the check for this in the function and it will respond just fine to plain vanilla incoming HTTP requests.

## Development

Develop new features by adding a test to [`handle_test.go`](handle_test.go) for each feature, and confirm it works with `go test`.

Update the running analog of the function using the `func` CLI or client library, and it can be invoked using a manually-created CloudEvent:

Using `curl`: 

```console
curl -v -X POST -d '{"input": "SALABOY"}' \
  -H'Content-type: application/json' \
  -H'Ce-id: 1' \
  -H'Ce-source: cloud-event-example' \
  -H'Ce-subject: Improve Content' \
  -H'Ce-type: UpperCasedEvent' \
  -H'Ce-specversion: 1.0' \
  http://localhost:8080/
```

Or using `httpie`:

```console
http -v "http://localhost:8080/" \
Content-Type:application/json \
Ce-Id:1 \
Ce-Subject:Improve \
Ce-Source:cloud-event-example \
Ce-Type:UpperCasedEvent \
Ce-Specversion:1.0 \
input="SALABOY"
```

For more, see [the complete documentation]('https://github.com/knative-sandbox/kn-plugin-func/tree/main/docs')

