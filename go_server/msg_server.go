package main

import (
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
)

type TestResult struct {
	MsgId    string  `json:"msg_id"`
	Start    float64 `json:"start"`
	End      float64 `json:"end"`
	Duration float64 `json:"duration"`
}

type TestResults []TestResult

func checkFileIsExist(filename string) bool {
	if _, err := os.Stat(filename); os.IsNotExist(err) {
		return false
	}
	return true
}

func writeResults(fileName, result string) {
	var f *os.File
	var err error
	if checkFileIsExist(fileName) {
		f, err = os.OpenFile(fileName, os.O_APPEND|os.O_WRONLY, 0666)
		if err != nil {
			fmt.Println("Open file fail", err)
		}
	} else {
		f, err = os.Create(fileName)
		if err != nil {
			fmt.Println("Create file fail", err)
		}
	}
	defer f.Close()
	_, err = io.WriteString(f, result+"\n")
	// _, err = f.Write(result)
	if err != nil {
		fmt.Printf("Error: %s", err.Error())
	}
}

func ReceiveMsg(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.Header().Add("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		// _, err := w.Write(responseBytes)
		// if nil != err {
		// 	return err
		// }
		return
	}
	defer func() {
		if err := r.Body.Close(); err != nil {
			fmt.Printf("failed to close request body (%s)", err)
		}
	}()
	// results := make(TestResults, 0)
	// dec := json.NewDecoder(r.Body)
	// err := dec.Decode(&results)
	// if err != nil {
	// 	fmt.Printf("Error: %s", err.Error())
	// }
	bodyBytes, err := ioutil.ReadAll(r.Body)
	println("Receive Msg: " + string(bodyBytes))
	if err != nil {
		fmt.Printf("Error: %s", err.Error())
	}

	writeResults("./test.txt", string(bodyBytes))
	w.Header().Add("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	io.WriteString(w, "Receive msg successfully.")
}

func main() {
	// Set routing rules
	http.HandleFunc("/", ReceiveMsg)

	//Use the default DefaultServeMux.
	err := http.ListenAndServe(":7777", nil)
	if err != nil {
		log.Fatal(err)
	}
}
