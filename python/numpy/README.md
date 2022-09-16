# Calculate the Euclidean distance using NumPy

Create a python function to calculate Euclidean distance using NumPy and deploy to Knative

## Prereqirements
- `knative` cluster is installed
- `func` is installed

## Create

Create the project with `func` command. Source codes will be created as below.
```
$ func create -l python numpy
Created python function in /home/ubuntu/knative-sandbox/func-tastic/python/fn

$ tree
.
└── numpy
    ├── func.py
    ├── func_test.py
    ├── func.yaml
    ├── Procfile
    ├── README.md
    └── requirements.txt
```

Then add the logic of alculating Euclidean distance using NumPy to the source code file `func.py`.

## Run and test locally

Run and test the function locally when finishing the development.

```
$ func run
   🙌 Function image built: docker.io/myrepo/python-numpy:latest
Detected function was already built.  Use --build to override this behavior.
Function started on port 8080
```
And then try to invoke from another terminal:
```
$func invoke --data '{"v1":"1 2","v2":"3 4"}'
```

## Build and deploy to server

Build the image and deploy to Knative cluster with below command.

```
$ func deploy
   🙌 Function image built: docker.io/daisyycguo/python-numpy:latest
   ✅ Function updated in namespace "default" and exposed at URL:
   http://python-numpy.default.example.com
$ kn service list
$ kn service list
NAME           URL                                       LATEST               AGE   CONDITIONS   READY   REASON
python-numpy   http://python-numpy.default.example.com   python-numpy-00010   1d    3 OK / 3     True
```

## Invoke with curl

The function now is invokable by curl.
```
$ curl -H "Host: python-numpy.default.example.com" -H 'Content-Type: application/json' http://1.2.3.4:32176 -d '{"v1":"3 4 5 6","v2":"3 4 5 6"}'
0.0
```
