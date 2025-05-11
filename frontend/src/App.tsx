import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";
import * as React from "react";
import { ChangeDates } from "./ChangeDate.tsx";
import { ChangesDataComponent } from "./ChangesDataComponent.tsx";
import { Container, Button, Row, Col } from "react-bootstrap";

const HandleDateClick = (event: React.MouseEvent<HTMLSpanElement>) => {
  const span = event.target as HTMLSpanElement;
  if (span.classList.contains("chosen")) {
    span.classList.remove("chosen");
  } else {
    const chosen_dates: HTMLCollectionOf<Element> =
      document.getElementsByClassName("chosen");
    if (chosen_dates.length >= 2) {
      chosen_dates[0].classList.remove("chosen");
    }
    span.classList.add("chosen");
  }
};

const App: React.FC = () => {
  const [array, setArray] = useState<Array<string>>([]),
    [dates, setDates] = useState<boolean>(true),
    [scraping, setScraping] = useState<boolean>(false),
    [error, setError] = useState<string>("");
  const fetchAPI = async () => {
    await axios.get("http://localhost/api/changes").then((response) => {
      setArray(response.data.last_10);
    });
  };
  useEffect(() => {
    fetchAPI();
  }, []);
  const HandleChangesButton = () => {
    setDates(false);
  };
  const HandleScrapeButton = async () => {
    setScraping(true);
    setError("");
    await axios.post("http://localhost/api/grab_data").then((response) => {
      if ("error" in response.data) {
        setError(response.data.error);
      } else {
        setError("");
      }
      setScraping(false);
      fetchAPI();
    });
  };
  return (
    /* This wraps the HTML in a single element without giving a specific one,
     *  making it turn into the parent element of <div id="root"> */
    <>
      {dates ? (
        <Container className="change-dates">
          <Row>
            <h1 className="text-center mb-5">SoFi position openings changes</h1>
          </Row>
          {scraping || error ? (
            <Row className="justify-content-center">
              <Col className="text-center">
                {error ? (
                  <span className="text-danger">{error}</span>
                ) : (
                  <span className="text-info">Scraping in process.</span>
                )}
              </Col>
            </Row>
          ) : null}
          <Row className="justify-content-center">
            <Col xs={4} className="text-center">
              <Button
                className="mx-auto"
                onClick={HandleScrapeButton}
                disabled={scraping}
              >
                Scrape positions
              </Button>
            </Col>
          </Row>
          <Row className="align-self-end">
            <h3 className="text-center">Please choose the period </h3>
          </Row>
          <Row>
            <Col xs={2}></Col>
            <Col xs={6}>
              <h5>The options to choose are:</h5>
              <ul>
                <li>Two dates: Period between them.</li>
                <li>
                  One date: The period is between it and the Friday before it.
                </li>
                <li>No date: The period will be since last Friday.</li>
              </ul>
            </Col>
          </Row>
          <Row>
            <Col xs={6} className="mx-auto">
              {array.map((item: string, i: number) => (
                <div key={i}>
                  <ChangeDates date={item} onClick={HandleDateClick} />
                </div>
              ))}
              <Button onClick={HandleChangesButton}>Request Changes</Button>
            </Col>
          </Row>
        </Container>
      ) : (
        <ChangesDataComponent />
      )}
    </>
  );
};

export default App;
