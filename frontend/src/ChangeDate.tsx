import * as React from "react";

interface Props {
    date: string;
    onClick: React.MouseEventHandler<HTMLSpanElement>;
}

export const ChangeDates: React.FC<Props> =({date, onClick})=> {
    const date_obj: Date = new Date(date),
          day: string = date_obj.toLocaleDateString('en-US', {weekday: 'long'});
    let date_res: string;
    if (day !== "Friday") {
        date_res = `${date} (${day})`;
    }
    else {
        date_res = date;
    }

    return (
        <span onClick={onClick}>{date_res}</span>
    )
};