package siteevent

import "encoding/json"

var (
	// NatsSubject is the base subject on which site events are published. The sub subjects contain the site id.
	// example: 'site-event.my-site'
	NatsSubject = "sites-event"
)

type Event struct {
	Train string `json:"train"`
	Event string `json:"event"`
	Site  string `json:"site"`
}

func Unmarshal(data []byte) (Event, error) {
	var event Event
	err := json.Unmarshal(data, &event)
	if err != nil {
		return event, err
	}
	return event, nil
}
