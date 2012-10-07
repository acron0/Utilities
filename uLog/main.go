package main

import (
	"fmt"
	"os"
	"net/http"
	"log"
	"regexp"
	"strings"
)

type route struct {
    pattern *regexp.Regexp
    handler http.Handler
}

type RegexpHandler struct {
    routes []*route
}

func (h *RegexpHandler) Handler(pattern *regexp.Regexp, handler http.Handler) {
    h.routes = append(h.routes, &route{pattern, handler})
}

func (h *RegexpHandler) HandleFunc(pattern *regexp.Regexp, handler func(http.ResponseWriter, *http.Request)) {
    h.routes = append(h.routes, &route{pattern, http.HandlerFunc(handler)})
}

func (h *RegexpHandler) HandleStrFunc(patternStr string, handler func(http.ResponseWriter, *http.Request)) {
	rx, err := regexp.Compile(patternStr);
	if err == nil {
		h.HandleFunc(rx, handler);
	}
}

func (h *RegexpHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    for _, route := range h.routes {
        if route.pattern.MatchString(r.URL.Path) {
            route.handler.ServeHTTP(w, r)
            return
        }
    }
    // no pattern matched; send 404 response
    http.NotFound(w, r)
}

/////////////////////////////////////////////////////////////////////////////

func printUsage() {
	fmt.Printf("Usage:");
	fmt.Printf("\tulog <port>\n");
}

type GlobalError struct {
	Message string
}

func (e *GlobalError) Error() string {
	return fmt.Sprintf("%s",e.Message);
}

func main() {

	version := 0.1;
	fmt.Printf("\nuLog - An external logging tool for Unity3D applications - v%g\n", version);

	args := os.Args;
	if len(args) < 2 {
		printUsage();
		return;
	}
	    
	err := startServer(args[1]);
	if err != nil {
		log.Fatal(err);
		printUsage();
		return;
	}
}

func startServer(portStr string) error {
			
	log.Print("[ULOG   ] Starting server on port " + portStr);
	
	// create regexp-based handler
	h := new( RegexpHandler)	

	// add functions
	h.HandleStrFunc("/log/.*$", logHandler);
	h.HandleStrFunc("/error/.*$", errorHandler);
	h.HandleStrFunc("/warn/.*$", warningHandler);
	h.HandleStrFunc("/crossdomain.xml$", crossDomainHandler);
	
	err := http.ListenAndServe(":"+portStr, h)
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
	
	return nil
}

func logHandler(w http.ResponseWriter, r *http.Request) {

	match := "/log/";
	i := strings.Index(r.URL.Path, match);
	if i != -1 {
		i += len(match);
		log.Print("[INFO   ] ", r.URL.Path[i:]    );
	}
}

func errorHandler(w http.ResponseWriter, r *http.Request) {

	match := "/error/";
	i := strings.Index(r.URL.Path, match);
	if i != -1 {
		i += len(match);
		log.Print("[ERROR  ] ", r.URL.Path[i:]    );
	}
}

func warningHandler(w http.ResponseWriter, r *http.Request) {

	match := "/warn/";
	i := strings.Index(r.URL.Path, match);
	if i != -1 {
		i += len(match);
		log.Print("[WARNING] ", r.URL.Path[i:]    );
	}
}
func crossDomainHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprint(w, "<cross-domain-policy><allow-access-from domain=\"*\"/></cross-domain-policy>");
}
