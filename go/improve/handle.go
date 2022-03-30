package function

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/cloudevents/sdk-go/v2/event"
	"github.com/google/uuid"

	cloudevents "github.com/cloudevents/sdk-go/v2"
)

type Output struct {
	Output    string `json:"output"`
	Input     string `json:"input"`
	Operation string `json:"operation"`
}

type Input struct {
	Input string `json:"input"`
}

func improve(event cloudevents.Event) (*event.Event, error) {
	inputOutput := Output{}
	err := json.Unmarshal(event.Data(), &inputOutput)
	if err != nil {
		fmt.Printf("%v\n", err)
		return nil, err
	}
	outputEvent := cloudevents.NewEvent()
	id, _ := uuid.NewUUID()
	outputEvent.SetID(id.String())
	outputEvent.SetSource("http://example.com/improved")
	outputEvent.SetType("ImprovedEvent")
	outputEvent.SetSubject("Content Improved!")
	output := Output{}
	output.Input = inputOutput.Output
	output.Output = inputOutput.Output + " improved!"
	output.Operation = "improve"
	outputEvent.SetData(cloudevents.ApplicationJSON, &output)

	fmt.Printf("Outgoing Event: %v\n", outputEvent)

	return &outputEvent, nil
}

// Handle an event.
func Handle(ctx context.Context, event cloudevents.Event) (*event.Event, error) {

	// Example implementation:
	fmt.Printf("Incoming Event: %v\n", event) // print the received event to standard output
	if event.Type() == "UpperCasedEvent" {
		return improve(event)
	}
	return nil, errors.New("No action for event type: " + event.Type())
}

/*
Other supported function signatures:

	Handle()
	Handle() error
	Handle(context.Context)
	Handle(context.Context) error
	Handle(event.Event)
	Handle(event.Event) error
	Handle(context.Context, event.Event)
	Handle(context.Context, event.Event) error
	Handle(event.Event) *event.Event
	Handle(event.Event) (*event.Event, error)
	Handle(context.Context, event.Event) *event.Event
	Handle(context.Context, event.Event) (*event.Event, error)

*/
