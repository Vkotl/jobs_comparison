import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";
import * as React from "react";
import {ChangeDates} from "./ChangeDate.tsx";
import {ChangesDataComponent} from "./ChangesDataComponent.tsx";
import {Container, Button, Row, Col} from "react-bootstrap";

const HandleDateClick = (event: React.MouseEvent<HTMLSpanElement>) => {
    const span = event.target as HTMLSpanElement;
    if (span.classList.contains("chosen")) {
        span.classList.remove("chosen");
    }
    else {
        const chosen_dates = document.getElementsByClassName("chosen");
        if (chosen_dates.length >= 2) {
            chosen_dates[0].classList.remove("chosen");
        }
        span.classList.add("chosen");
    }
}

const App: React.FC = () => {
    const [array, setArray] = useState([]);
    const [dates, setDates] = React.useState(true);
    const fetchAPI = async () => {
      const response = await axios.get("http://localhost:3000/changes");
      setArray(response.data.last_10);
    };
    useEffect(() => {
        fetchAPI();
    }, []);
    const HandleChangesButton = () => {
        setDates(false)
    }
  return (
    /* This wraps the HTML in a single element without giving a specific one,
    *  making it turn into the parent element of <div id="root"> */
      <>
      {dates ? (
          <Container className="change-dates">
              <h1 className="text-center mb-5">SoFi position openings changes</h1>
              <h3 className="text-center">Please choose the period </h3>
              <Row>
                  <Col xs={2}></Col>
                  <Col xs={6}>
                      <h5>The options to choose are:</h5>
                      <ul>
                          <li>Two dates: Period between them.</li>
                          <li>One date: The period is between it and the
                              Friday before it.
                          </li>
                          <li>No date: The period will be since last Friday.
                          </li>
                      </ul>
                  </Col>
              </Row>
              <Row>
                  <Col xs={6} className={"mx-auto"}>
                      {array.map((item, i) => (
                          <div key={i}>
                              <ChangeDates date={item} onClick={HandleDateClick}/>
                          </div>
                      ))}
                      <Button onClick={HandleChangesButton}>Request Changes</Button>
                  </Col>
              </Row>
          </Container>
      ) : (
          <ChangesDataComponent/>
      )}
      </>
  )
}

export default App
