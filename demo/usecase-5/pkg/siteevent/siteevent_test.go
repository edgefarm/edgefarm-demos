package siteevent

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestUpdateConfigFile(t *testing.T) {
	assert := assert.New(t)
	j := `{
	"train": "mytrain",
	"event": "leaving",
	"site": "mysite"
}`
	event, err := Unmarshal([]byte(j))
	assert.Nil(err)
	assert.Equal("mytrain", event.Train)
	assert.Equal("leaving", event.Event)
	assert.Equal("mysite", event.Site)
}
