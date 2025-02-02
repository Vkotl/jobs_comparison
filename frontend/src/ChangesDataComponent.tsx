import * as React from "react";
import {useState} from "react";
import axios from "axios";
import {Col, Container, Row} from "react-bootstrap";
import {ChangesJsonData} from "./interfaces/Company.ts";
import {ChangesGroup} from "./ChangesGroup.tsx";
import sofiLogo from "./assets/sofi_logo.svg";
import galileoLogo from "./assets/galileo_logo.svg";

export const ChangesDataComponent: React.FC = ()=> {
    const [changes, setChanges] = useState<ChangesJsonData | null>(null),
        chosen: HTMLCollectionOf<Element> = document.getElementsByClassName("chosen"),
        is_dates: boolean = document.getElementsByClassName("change-dates").length > 0;
    let decision: string | undefined = undefined;
    if (chosen.length == 0 && is_dates) {
        decision = "week";
    }
    else if (chosen.length == 1) {
        decision = chosen[0].textContent || "week";
        decision = decision.replace(/-/g, "");
    }
    else if (chosen.length == 2) {
        const first: string = chosen[0].textContent || "First date had a problem.",
            second: string = chosen[1].textContent || "Second date had a problem.";
        decision = `${first.replace(/-/g, "")}-${second.replace(/-/g, "")}`;
    }
    if (decision !== undefined) {
        axios.get("http://localhost:3000/changes/"+decision
        ).then((response) => {
            setChanges(response.data);
        });
    }
    return (
        <>
            {changes ? (
                <Container id="changes-container">
                    <Row className="text-center">
                        <Col xs={12} className="position-relative">
                            <img src={sofiLogo} alt="SoFi's logo"/>
                            <h2>changes between {changes.previous_date.replace(/-/g,".")} and {changes.new_date.replace(/-/g, ".")}</h2>
                        </Col>
                    </Row>
                    <Row className="justify-content-center">
                        <Col>
                            <ChangesGroup data={changes} company="sofi" pos_type="new" />
                        </Col>
                    </Row>
                    <Row className="justify-content-center">
                        <Col>
                            <ChangesGroup data={changes} company="sofi" pos_type="removed" />
                        </Col>
                    </Row>
                    <Row className="text-center">
                        <Col xs={12} className="position-relative">
                            <img src={galileoLogo} alt="Galileo Logo"/>
                            <h2>changes between {changes.previous_date.replace(/-/g,".")} and {changes.new_date.replace(/-/g, ".")}</h2>
                        </Col>
                    </Row>
                    <Row className="justify-content-center">
                        <Col>
                            <ChangesGroup data={changes} company="galileo" pos_type="new" />
                        </Col>
                    </Row>
                    <Row className="justify-content-center">
                        <Col>
                            <ChangesGroup data={changes} company="galileo" pos_type="removed" />
                        </Col>
                    </Row>
                </Container>
            ) : (
                <div></div>
            )}
        </>
    );
}