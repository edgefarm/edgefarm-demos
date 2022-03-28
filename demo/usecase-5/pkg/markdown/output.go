package markdown

import (
	"fmt"
	"os"

	tablewriter "github.com/fbiville/markdown-table-formatter/pkg/markdown"
)

var (
	header       []string = []string{"DATE", "SITE", "TRAIN", "EVENT"}
	emptyFileStr          = `---
title: Home
layout: home
---

# Incoming and leaving trains log

`
)

type Markdown struct {
	table [][]string
	path  string
}

func NewMarkdown(path string) (*Markdown, error) {
	_, err := os.Create(path)
	if err != nil {
		return nil, err
	}
	m := &Markdown{
		table: [][]string{},
		path:  path,
	}
	return m, nil
}

func (m *Markdown) Add(row []string) {
	m.table = append([][]string{row}, m.table...)
}

func (m *Markdown) Print() error {
	err := m.clearFile()
	if err != nil {
		return err
	}
	err = m.writeString(emptyFileStr)
	if err != nil {
		return err
	}
	err = m.writeTable()
	if err != nil {
		return err
	}
	return nil
}

func (m *Markdown) clearFile() error {
	err := os.Truncate(m.path, 0)
	if err != nil {
		return err
	}
	return nil
}

func (m *Markdown) writeTable() error {
	f, err := os.OpenFile(m.path, os.O_APPEND|os.O_WRONLY, 0600)
	if err != nil {
		return err
	}
	defer f.Close()

	str, err := tablewriter.NewTableFormatterBuilder().Build(header...).Format(m.table)
	if err != nil {
		return err
	}
	fmt.Println(str)

	_, err = f.Write([]byte(str))
	if err != nil {
		return err
	}
	return nil
}

func (m *Markdown) writeString(str string) error {
	f, err := os.OpenFile(m.path, os.O_APPEND|os.O_WRONLY, 0600)
	if err != nil {
		return err
	}
	defer f.Close()
	_, err = f.WriteString(str)
	if err != nil {
		return err
	}

	return nil
}
