import * as React from "react";
import {DepartmentData} from "./DepartmentData.tsx";
import {ChangesJsonData, Company} from "./interfaces/Company.ts";

interface Props {
    data: ChangesJsonData;
    company: keyof Pick<ChangesJsonData, "sofi" | "galileo">;
    pos_type: keyof Company;
}

export const ChangesGroup: React.FC<Props> = ({data, company, pos_type})=> {
    const capitalized: string = pos_type.charAt(0).toUpperCase() + pos_type.slice(1, pos_type.length);
    return (
        <>
            <h3>{capitalized.concat(" ", "Positions:")}</h3>
            <div className="change-group">
                {
                    Object.keys(data[company][pos_type]).map((department: string) => (
                        <DepartmentData department={department}
                                        departments={data[company][pos_type]}
                                        link={pos_type !== "removed"}
                                        key={department.concat(" ", pos_type)}/>
                    ))
                }
            </div>
        </>
    )
};