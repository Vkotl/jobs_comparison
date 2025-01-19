import * as React from "react";
import axios from "axios";
import {ChangesJsonData} from "./interfaces/Company.ts";
import {useState} from "react";
import {Col, Container, Row} from "react-bootstrap";
import sofiLogo from "./assets/sofi_logo.svg";
import galileoLogo from "./assets/galileo_logo.svg";
import {ChangesGroup} from "./ChangesGroup.tsx";

export const ChangesDataComponent: React.FC = ()=> {
    const [changes, setChanges] = useState<ChangesJsonData | null>(null);
    const chosen = document.getElementsByClassName("chosen");
    if (chosen.length == 2) {
        const first: string = chosen[0].textContent || "First date had a problem.",
              second: string = chosen[1].textContent || "Second date had a problem.",
              decision: string = first.replace(/-/g, "").concat("-", second.replace(/-/g, ""));
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
                            <img src={sofiLogo}/>
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
                            <img src={galileoLogo}/>
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