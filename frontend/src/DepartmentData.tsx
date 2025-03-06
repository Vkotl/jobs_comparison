import * as React from "react";

interface Props {
  department: string;
  departments: { [key: string]: [[string, string, boolean]] };
  link: boolean;
}

export const DepartmentData: React.FC<Props> = ({
  department,
  departments,
  link,
}) => {
  const position_classes = (flag: boolean) => {
    const classes: string = "position";
    return flag ? `${classes} new-position` : classes;
  };
  return (
    <div className="department">
      <h4>{department}</h4>
      <ul>
        {departments[department].map(
          (position: [string, string, boolean], i: number) => (
            <li className={position_classes(position[2])} key={i}>
              {position[1] !== "" && link ? (
                <a href={position[1]} target="_blank" rel="noopener noreferrer">
                  {position[0]}
                </a>
              ) : (
                position[0]
              )}
            </li>
          ),
        )}
      </ul>
    </div>
  );
};
