package eventlistener

import "encoding/json"

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
