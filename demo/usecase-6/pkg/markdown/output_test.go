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
	assert.Nil(m.Add(row))
	row = []string{"hello", "foo", "bar", "mytes"}
	assert.Nil(m.Add(row))
	m.Print()
	fmt.Println(file.Name())

	data, err := ioutil.ReadFile(file.Name())
	assert.Nil(err)
	assert.Equal(string(data),
		`+-------+------+-------+-------+
| DATE  | SITE | TRAIN | EVENT |
+-------+------+-------+-------+
| a     | b    | c     | d     |
| hello | foo  | bar   | mytes |
+-------+------+-------+-------+
`)
}
