package markdown

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestMarkdown(t *testing.T) {
	assert := assert.New(t)

	file, err := ioutil.TempFile("", "")
	if err != nil {
		log.Fatal(err)
	}
	defer os.Remove(file.Name())

	row := []string{"a", "b", "c", "d"}

	m, err := NewMarkdown(file.Name())
	assert.Nil(err)
	m.Add(row)
	row = []string{"hello", "foo", "bar", "mytes"}
	m.Add(row)
	assert.Nil(m.Print())
	fmt.Println(file.Name())

	data, err := ioutil.ReadFile(file.Name())
	assert.Nil(err)
	fmt.Println(string(data))
	assert.Equal(string(data),
		`---
title: Home
layout: home
---

# Incoming and leaving trains log

| DATE | SITE | TRAIN | EVENT |
| ---- | ---- | ----- | ----- |
| hello | foo | bar | mytes |
| a | b | c | d |
`)
}
