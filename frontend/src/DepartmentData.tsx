import * as React from "react";

interface Props {
    department: string;
    departments: {[key: string]: string[]};
}

export const DepartmentData: React.FC<Props> = ({department, departments})=> {
    return (
        <div className="department">
            <h4>{department}</h4>
            <ul>
            {
                departments[department].map((position: string, i: number) => (
                    <li className="position" key={i}>{position}</li>
                ))
            }
            </ul>
        </div>
    )
};