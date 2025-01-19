import * as React from "react";

interface Props {
    date: string;
    onClick: React.MouseEventHandler<HTMLSpanElement>;
}

export const ChangeDates: React.FC<Props> =({date, onClick})=> {
    return (
        <span onClick={onClick}>{date}</span>
    )
};