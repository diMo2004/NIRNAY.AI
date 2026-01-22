import delay from "./api";

export const getReportById = async (id) => {
  await delay(500);

  return {
    problem: "Sample problem from user",
    legitimacy: "YES",
    confidence: "82%",
    discrepancies: [
      "Process inefficiency",
      "Lack of automation",
      "User inconvenience"
    ],
    ideas: [
      {
        title: "Automation Tool",
        description: "A platform to automate the process"
      },
      {
        title: "Mobile App Solution",
        description: "User friendly app to reduce friction"
      }
    ]
  };
};

export const getAllReports = async () => {
  await delay(500);

  return [
    { id: 1, title: "Hospital queue problem", date: "20 Jan 2026" },
    { id: 2, title: "Traffic management issue", date: "18 Jan 2026" }
  ];
};
