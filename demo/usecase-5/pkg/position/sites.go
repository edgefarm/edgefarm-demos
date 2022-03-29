package position

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"

	"github.com/nats-io/nats.go"
)

type SiteManager struct {
	siteStateFile string
}

type SiteInfo struct {
	SiteId string        `json:"id"`
	Zero   Coordinates   `json:"zero"`
	Area   []Coordinates `json:"area"`
}

var (
	RegisterSiteNatsTopic = "site.register"
)

func createEmptyStatesFile(path string) error {
	if err := ioutil.WriteFile(path, []byte("{}"), 0644); err != nil {
		return fmt.Errorf("Cannot create file %v", err)
	}
	return nil
}

// NewSiteManager will return an new SiteManager object. The state file can be passed by env variable SITES_STATE_FILE.
// If no state file is passed, a temporary file will be created.
func NewSiteManager() (*SiteManager, error) {
	// if env variable SITES_STATE_FILE is set, then use this
	if env := os.Getenv("SITES_STATE_FILE"); len(env) > 0 {
		if _, err := os.Stat(env); os.IsNotExist(err) {
			basepath := filepath.Dir(env)
			err := os.MkdirAll(basepath, 0755)
			if err != nil {
				return nil, fmt.Errorf("Cannot create directory %v", err)
			}
			err = createEmptyStatesFile(env)
			if err != nil {
				return nil, fmt.Errorf("Cannot create file %v", err)
			}
		}
		// prepare file if empty
		fileContent, err := os.ReadFile(env)
		if err != nil {
			return nil, fmt.Errorf("Cannot read file %v", err)
		}
		if string(fileContent) == "" {
			err = createEmptyStatesFile(env)
			if err != nil {
				return nil, fmt.Errorf("Cannot create file %v", err)
			}
		}
		return &SiteManager{
			siteStateFile: env,
		}, nil
		// else generate temp file and use this
	} else {
		siteStateFile, err := ioutil.TempFile(os.TempDir(), "siteStateFile-")
		if err != nil {
			return nil, fmt.Errorf("Cannot create temporary file %v", err)
		}
		defer siteStateFile.Close()
		// write empty state to file
		if _, err := siteStateFile.Write([]byte("{}")); err != nil {
			return nil, fmt.Errorf("Failed to write to temporary file %v", err)
		}
		return &SiteManager{
			siteStateFile: siteStateFile.Name(),
		}, nil
	}
}

func (c *SiteManager) RegisterHandler(msg *nats.Msg) {

	fmt.Println("Received register request: ", string(msg.Data))

	// Convert message to SiteInfo
	var siteInfo SiteInfo
	if err := json.Unmarshal(msg.Data, &siteInfo); err != nil {
		log.Printf("Error occured during unmarshaling. Error:  %v", err)
		return
	}
	// Register site
	if err := c.RegisterSite(siteInfo); err != nil {
		log.Printf("Error occured during registering site. Error:  %v", err)
		return
	}
}

func (s *SiteManager) RegisterSite(siteInfo SiteInfo) error {
	// read current state from file
	siteStateByte, err := os.ReadFile(s.siteStateFile)
	if err != nil {
		return fmt.Errorf("Cannot read site state file %v", err)
	}
	// convert to map
	var siteMap map[string]SiteInfo
	if err := json.Unmarshal(siteStateByte, &siteMap); err != nil {
		return fmt.Errorf("Error occured during unmarshaling. Error:  %v", err)
	}

	// add or update site id map
	siteMap[siteInfo.SiteId] = siteInfo

	newSiteStateByte, err := json.Marshal(siteMap)
	if err != nil {
		return fmt.Errorf("Error occured during marshaling. Error:  %v", err)
	}

	// store new content to file
	if err := ioutil.WriteFile(s.siteStateFile, newSiteStateByte, 0644); err != nil {
		return fmt.Errorf("Cannot write site state file %v", err)
	}
	return nil
}

func (s *SiteManager) getZeroPoint(siteId string) (Coordinates, error) {
	// read current state from file
	siteStateByte, err := os.ReadFile(s.siteStateFile)
	if err != nil {
		return Coordinates{}, fmt.Errorf("Cannot read site state file %v", err)
	}

	// convert to map
	var siteMap map[string]SiteInfo
	if err := json.Unmarshal(siteStateByte, &siteMap); err != nil {
		return Coordinates{}, fmt.Errorf("Error occured during unmarshaling. Error:  %v", err)
	}
	// get zero point
	siteInfo, ok := siteMap[siteId]
	if !ok {
		return Coordinates{}, fmt.Errorf("Site %s not found", siteId)
	}
	return siteInfo.Zero, nil
}
