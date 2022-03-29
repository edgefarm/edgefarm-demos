package position

import (
	"fmt"
	"math"
)

const (
	TraceletNatsSubject = "train.tracelet"
	GpsNatsSubject      = "train.gps"
	// radius of the earth in kilometer required to calculate meter to coordinatess
	earth = 6378.137
)

type Coordinates struct {
	Lat float64 `json:"lat"`
	Lon float64 `json:"lng"`
}

type GpsMessage struct {
	ID          string      `json:"id"`
	Coordinates Coordinates `json:"coordinates"`
}

type TraceletMessage struct {
	X       float64 `json:"x"`
	Y       float64 `json:"y"`
	SiteID  string  `json:"site-id"`
	TrainID string  `json:"train-id"`
}

type Position struct {
	Lat  float64 `json:"lat"`
	Lon  float64 `json:"lon"`
	Hres bool    `json:"hres"`
}

type TrainPosition struct {
	ID       string   `json:"id"`
	SiteID   string   `json:"site-id"`
	Position Position `json:"position"`
}

// GpsToTrainPositon convert GpsMessage to Position struct
func GpsToTrainPositon(gpsData GpsMessage) TrainPosition {
	return TrainPosition{
		ID:       gpsData.ID,
		SiteID:   "",
		Position: Position{Lat: gpsData.Coordinates.Lat, Lon: gpsData.Coordinates.Lon, Hres: false},
	}
}

// TraceletToTrainPosition convert TraceletMessage to Position struct
func TraceletToTrainPosition(traceletData TraceletMessage, siteManager *SiteManager) (TrainPosition, error) {
	// get zero point of tracelet id from database
	zero, error := siteManager.getZeroPoint(traceletData.SiteID)
	if error != nil {
		return TrainPosition{}, fmt.Errorf("Error occured during getting zero point. Error: %s", error.Error())
	}
	// calculate position
	return TrainPosition{
		ID:       traceletData.TrainID,
		SiteID:   traceletData.SiteID,
		Position: Position{Lat: zero.Lat + (float64(traceletData.Y)/earth/1000)*(180/math.Pi), Lon: zero.Lon + (float64(traceletData.X)/earth/1000)*(180/math.Pi)/math.Cos(zero.Lat*math.Pi/180), Hres: true},
	}, nil
}
