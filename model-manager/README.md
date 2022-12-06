# How to deploy the model-manager locally
1. Create an environment
```
conda create --name model-manager python==3.7
```

2. Install the dependencies and development dependencies in your environment
```
conda activate model-manager
make install
make install-dev
```

3. Setup the local authentication. The command below will create a file called `private_key.pem` in the root of the project will print a token.
```
make auth
```
You can see the token again by running `make token`

4. Build the project (you may need sudo because it will run docker. Only if your user doesn't have permissions to run docker)
```
make build
```

5. Bring up the model! (you may need sudo because it will run docker. Only if your user doesn't have permissions to run docker)
```
make up
```