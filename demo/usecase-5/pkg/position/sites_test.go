package position

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

var (
	registeredSite string = `{"site1":{"id":"site1","zero":{"lat":49.44452758496568,"lng":11.079950588826692},"area":[{"lat":49.44452758496568,"lng":11.079950588826692},{"lat":49.44564326546803,"lng":11.079950588826692},{"lat":49.44564326546803,"lng":11.083815851373487},{"lat":49.44452758496568,"lng":11.083815851373487}]}}`
)

func prepare(registeredSites string) *os.File {
	tmpFile, err := ioutil.TempFile(os.TempDir(), "prefix-")
	if err != nil {
		log.Fatal("Cannot create temporary file", err)
	}
	text := []byte(registeredSites)
	if _, err = tmpFile.Write(text); err != nil {
		log.Fatal("Failed to write to temporary file", err)
	}

	return tmpFile
}

func cleanup(file *os.File) {
	// Close the file
	if err := file.Close(); err != nil {
		log.Fatal(err)
	}
	os.Remove(file.Name())
}

// TestRegisterSite tests the RegisterSite function
func TestRegisterSite(t *testing.T) {
	assert := assert.New(t)
	sm, err := NewSiteManager()
	assert.Nil(err)

	sm.RegisterSite(SiteInfo{
		SiteId: "site1",
		Zero:   Coordinates{Lat: 49.44452758496568, Lon: 11.079950588826692},
		Area: []Coordinates{
			{Lat: 49.44452758496568, Lon: 11.079950588826692},
			{Lat: 49.44564326546803, Lon: 11.079950588826692},
			{Lat: 49.44564326546803, Lon: 11.083815851373487},
			{Lat: 49.44452758496568, Lon: 11.083815851373487},
		},
	})

	expectedFileContent := `{"site1":{"id":"site1","zero":{"lat":49.44452758496568,"lng":11.079950588826692},"area":[{"lat":49.44452758496568,"lng":11.079950588826692},{"lat":49.44564326546803,"lng":11.079950588826692},{"lat":49.44564326546803,"lng":11.083815851373487},{"lat":49.44452758496568,"lng":11.083815851373487}]}}`

	// read file content
	fileContent, err := os.ReadFile(sm.siteStateFile)
	assert.Nil(err)
	assert.Equal(expectedFileContent, string(fileContent))
}

// TestRegisterSiteUpdate tests the RegisterSite function with an existing site which is updated
func TestRegisterSiteUpdate(t *testing.T) {
	assert := assert.New(t)

	// prepare sitemanager with existing site
	file := prepare(registeredSite)
	sm := SiteManager{siteStateFile: file.Name()}

	// update existing site
	siteInfo := SiteInfo{
		SiteId: "site1",
		Zero:   Coordinates{Lat: 49.55552758496568, Lon: 11.079950588826692},
		Area: []Coordinates{
			{Lat: 49.55552758496568, Lon: 11.079950588826692},
			{Lat: 49.55664326546803, Lon: 11.079950588826692},
			{Lat: 49.55664326546803, Lon: 11.083815851373487},
			{Lat: 49.55552758496568, Lon: 11.083815851373487},
		},
	}
	sm.RegisterSite(siteInfo)

	info, err := json.Marshal(siteInfo)
	fmt.Println(info)

	expectedFileContent := `{"site1":{"id":"site1","zero":{"lat":49.55552758496568,"lng":11.079950588826692},"area":[{"lat":49.55552758496568,"lng":11.079950588826692},{"lat":49.55664326546803,"lng":11.079950588826692},{"lat":49.55664326546803,"lng":11.083815851373487},{"lat":49.55552758496568,"lng":11.083815851373487}]}}`

	// read file content
	fileContent, err := os.ReadFile(sm.siteStateFile)
	assert.Nil(err)
	assert.Equal(expectedFileContent, string(fileContent))

	cleanup(file)
}

// TestRegisterSiteAddSecond tests the RegisterSite function with an existing site by adding another site
func TestRegisterSiteAddSecond(t *testing.T) {
	assert := assert.New(t)

	// prepare sitemanager with existing site
	file := prepare(registeredSite)
	sm := SiteManager{siteStateFile: file.Name()}

	// update existing site
	sm.RegisterSite(SiteInfo{
		SiteId: "site2",
		Zero:   Coordinates{Lat: 49.55552758496568, Lon: 11.079950588826692},
		Area: []Coordinates{
			{Lat: 49.55552758496568, Lon: 11.079950588826692},
			{Lat: 49.55664326546803, Lon: 11.079950588826692},
			{Lat: 49.55664326546803, Lon: 11.083815851373487},
			{Lat: 49.55552758496568, Lon: 11.083815851373487},
		},
	})

	expectedFileContent := `{"site1":{"id":"site1","zero":{"lat":49.44452758496568,"lng":11.079950588826692},"area":[{"lat":49.44452758496568,"lng":11.079950588826692},{"lat":49.44564326546803,"lng":11.079950588826692},{"lat":49.44564326546803,"lng":11.083815851373487},{"lat":49.44452758496568,"lng":11.083815851373487}]},"site2":{"id":"site2","zero":{"lat":49.55552758496568,"lng":11.079950588826692},"area":[{"lat":49.55552758496568,"lng":11.079950588826692},{"lat":49.55664326546803,"lng":11.079950588826692},{"lat":49.55664326546803,"lng":11.083815851373487},{"lat":49.55552758496568,"lng":11.083815851373487}]}}`

	// read file content
	fileContent, err := os.ReadFile(sm.siteStateFile)
	assert.Nil(err)
	assert.Equal(expectedFileContent, string(fileContent))

	cleanup(file)
}
