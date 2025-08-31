package protocol

import (
	"bytes"
)

func WriteWithPadding(buf *bytes.Buffer, value string, size int) {
	// Convert string to byte slice
	data := []byte(value)
	if len(data) < size {
		padding := make([]byte, size-len(data))
		// Fill up space left using null bytes
		data = append(data, padding...)
	}

	buf.Write(data)
}