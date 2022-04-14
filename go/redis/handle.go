package function

import (
	"context"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"

	"github.com/go-redis/redis"
)

var redisHost = os.Getenv("REDIS_HOST")



// Handle an HTTP Request.
func Handle(ctx context.Context, res http.ResponseWriter, req *http.Request) {
	client := redis.NewClient(&redis.Options{
		Addr:     redisHost,
		Password: "",
		DB:       0,
	})

	/*
	* Use client to write and read data from Redis
	 */

	body, err := ioutil.ReadAll(req.Body)
	if err != nil {
		log.Printf("Error reading body: %v", err)
		http.Error(res, "can't read body", http.StatusBadRequest)
		return
	}


	_, err = client.RPush("my-key", "echo" + string(body)).Result()
	if err != nil {
		http.Error(res, "can't push key to redis", http.StatusBadRequest)
		return
	}

	result, err := client.LRange("my-key", 0, -1).Result()
	if err != nil {
		http.Error(res, "can't read key from redis", http.StatusBadRequest)
		return
	}
	for _, value := range result {
		fmt.Fprintln(res, value)

	}



}
