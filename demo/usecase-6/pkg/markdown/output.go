package markdown

import (
	"bufio"
	"os"

	"github.com/olekukonko/tablewriter"
)

var (
	header []string = []string{"DATE", "SITE", "TRAIN", "EVENT"}
)

type Markdown struct {
	Title       string
	Table       [][]string
	tablewriter *tablewriter.Table
	writer      *bufio.Writer
	path        string
}

func NewMarkdown(path string) (*Markdown, error) {
	f, err := os.Create(path)
	if err != nil {
		return nil, err
	}

	writer := bufio.NewWriter(f)
	m := &Markdown{
		Table:  [][]string{},
		writer: writer,
		path:   path,
	}
	m.tablewriter = tablewriter.NewWriter(m.writer)
	m.tablewriter.SetHeader(header)
	m.tablewriter.SetAlignment(tablewriter.ALIGN_LEFT)
	return m, nil
}

func (m *Markdown) Add(row []string) error {
	m.tablewriter.Append(row)
	return nil
}

func (m *Markdown) Print() {
	m.tablewriter.Render()
	os.Truncate(m.path, 0)
	m.writer.Flush()

}
