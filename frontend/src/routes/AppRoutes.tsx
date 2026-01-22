import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import NewAnalysis from "../pages/NewAnalysis";
import Report from "../pages/Report";
import History from "../pages/History";
import Progress from "../pages/progress";


import DashboardLayout from "../components/layout/DashboardLayout";

const AppRoutes = () => {
  return (
    <BrowserRouter>
      <Routes>

        <Route
          path="/"
          element={
            <DashboardLayout>
              <NewAnalysis />
            </DashboardLayout>
          }
        />

        <Route
          path="/new-analysis"
          element={
            <DashboardLayout>
              <NewAnalysis />
            </DashboardLayout>
          }
        />

        <Route
  path="/progress"
  element={
    <DashboardLayout>
      <Progress />
    </DashboardLayout>
  }
/>

        <Route
          path="/report/:id"
          element={
            <DashboardLayout>
              <Report />
            </DashboardLayout>
          }
        />

        <Route
          path="/history"
          element={
            <DashboardLayout>
              <History />
            </DashboardLayout>
          }
        />

      </Routes>
    </BrowserRouter>
  );
};

export default AppRoutes;
