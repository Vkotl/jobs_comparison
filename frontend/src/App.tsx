import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";
import * as React from "react";
import {ChangeDates} from "./ChangeDate.tsx";
import {ChangesDataComponent} from "./ChangesDataComponent.tsx";
import {Container, Button} from "react-bootstrap";

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
                {array.map((item, i) => (
                    <div key={i}>
                        <ChangeDates date={item} onClick={HandleDateClick} />
                    </div>
                ))}
                <Button onClick={HandleChangesButton} >Request Changes</Button>
            </Container>
        ) : (
            <ChangesDataComponent />
        )}

    </>
  )
}

export default App
