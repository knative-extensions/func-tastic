# HTTP Function for Image Recognition Inference with TensorFlow

This sample project shows an HTTP function for real-time image recognition inference 
with TensorFlow on a pretrained model(ResNet50).

The function(`func.py`) is based on class `ImageRecognitionService`(`image_recognition_service.py`). This class defines several functions for data preprocessing, running inference and inference result parsing using optimized TensorFlow.

## Endpoints

Running this function will expose three endpoints.

  - `/` The endpoint for inference.
    - GET request will receive a response with the inference result of a test image(data/test.JPEG)
    - POST request need to give an image URL in JSON format(`{'imgURL':'your custom URL'}`), and the response will give human-read inference result of the image
  - `/health/readiness` The endpoint for a readiness health check
  - `/health/liveness` The endpoint for a liveness health check

## Testing

This function project includes three test functions in [unit test](./test_func.py):
- test GET request
- test POST request
- test empty request

```bash
$ python test_func.py
```

## Create funtion
Requirements:
- [func](https://github.com/knative/func) is installed

```bash
$ cd func-tastic/python
$ func create -l python tensorflow/image-recognition
$ cd tensorflow/image_recognition
$ tree
.
└── image-recognition
    ├── func.py
    ├── func_test.py
    ├── func.yaml
    ├── Procfile
    ├── README.md
    └── requirements.txt
```
Then add the logic of request handler and image recgnition inference to:
- `func.py`
- `image_recognition_service.py`

## Build and run locally

```bash
$ func build -i docker.io/chzhyang/tensorflow-image-recognition:latest
$ func run
  🙌 Function image built: docker.io/chzhyang/tensorflow-image-recognition:latest
Detected function was already built.  Use --build to override this behavior.
Function started on port 8080
Load model...
...
Cache model...
...
Ready for inference... 
```

## Function invocation

- Send POST request using `func invoke`

```bash
$ func invoke --data '{"imgURL": "https://raw.githubusercontent.com/chzhyang/faas-workloads/main/tensorflow/image_recognition/tensorflow_image_classification/data/ILSVRC2012_test_00000181.JPEG"}'
{"top_predictions": [["king penguin, Aptenodytes patagonica", "drake", "albatross, mollymawk", "toucan", "guenon, guenon monkey"]]}
```

- Send GET and POST request using `curl`

```bash
curl http://127.0.0.1:8080
{"top_predictions": [["king penguin, Aptenodytes patagonica", "drake", "albatross, mollymawk", "toucan", "guenon, guenon monkey"]]}

$ curl -X POST http://127.0.0.1:8080 \
-H "Content-Type: application/json"  \
-d '{"imgURL": "https://raw.githubusercontent.com/chzhyang/faas-workloads/main/tensorflow/image_recognition/tensorflow_image_classification/data/ILSVRC2012_test_00000181.JPEG"}'
{"top_predictions": [["king penguin, Aptenodytes patagonica", "drake", "albatross, mollymawk", "toucan", "guenon, guenon monkey"]]}
```


## Deploy function into Knative cluster

Requirements:
- [func](https://github.com/knative/func) is installed
- [Knative](https://knative.dev/docs/) is installed

```bash
$ func deploy -i docker.io/chzhyang/tensorflow-image-recognition:latest
    🙌 Function image built: docker.io/chzhyang/tensorflow-image-recognition:latest
    ✅ Function deployed in namespace "default" and exposed at URL:
    http://tensorflow-image-recognition.default.example.com
```

## Cleanup

To remove the deployed function from your cluster, run:

```bash
func delete
```
