package position

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

// TestTracetletToPosition calls tracetletToPosition and compares the result with the expected result
func TestTracetletToTrainPosition(t *testing.T) {
	assert := assert.New(t)

	// prepare sitemanager with existing site
	file := prepare(registeredSite)
	sm := SiteManager{siteStateFile: file.Name()}

	tm := TraceletMessage{
		X:       280,
		Y:       124,
		SiteID:  "site1",
		TrainID: "my-super-train",
	}

	// pre-check if zero point can be found correctly
	zero, err := sm.getZeroPoint("site1")
	assert.Nil(err)
	assert.Equal(Coordinates{Lat: 49.44452758496568, Lon: 11.079950588826692}, zero)

	// Checked with https://rechneronline.de/geo-coordinates/#distance
	tp, err := TraceletToTrainPosition(tm, &sm)
	assert.Nil(err)
	assert.Equal(49.44564149591798, tp.Position.Lat)
	assert.Equal(11.083819159855292, tp.Position.Lon)
	assert.Equal(true, tp.Position.Hres)
	assert.Equal("my-super-train", tp.ID)
	cleanup(file)
}
