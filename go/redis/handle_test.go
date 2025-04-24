package function

import (
	"context"
	"fmt"
	"github.com/alicebob/miniredis"
	"io/ioutil"
	"log"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"testing"
)

// TestHandle ensures that Handle executes without error and returns the
// HTTP 200 status code indicating no errors.
func TestHandle(t *testing.T) {
	mr, err := miniredis.Run()
	if err != nil {
		log.Fatalf("an error '%s' was not expected when opening a stub database connection", err)
	}

	os.Setenv("REDIS_HOST", mr.Addr())

	var (
		w = httptest.NewRecorder()

		req = httptest.NewRequest("POST", "http://example.com/test", strings.NewReader("hello world"))

		res *http.Response
	)

	// Invoke the Handler via a standard Go http.Handler
	func(w http.ResponseWriter, req *http.Request) {
		Handle(context.Background(), w, req)
	}(w, req)

	res = w.Result()
	defer res.Body.Close()

	body, err := ioutil.ReadAll(res.Body)

	fmt.Println(string(body))

	// Assert postconditions
	if err != nil {
		t.Fatalf("unepected error in Handle: %v", err)
	}
	if res.StatusCode != 200 {
		t.Fatalf("unexpected response code: %v", res.StatusCode)
	}
}
