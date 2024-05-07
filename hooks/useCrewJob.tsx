"use client";

import axios from "axios";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";

export type EventType = {
  data: string;
  timestamp: string;
};

export type EmailDraftInfo = {
  email: string;
};

export const useCrewJob = () => {
  // State
  const [running, setRunning] = useState<boolean>(false);
  const [first_name, setfirst_name] = useState<string[]>([]);
  const [last_name, setlast_name] = useState<string[]>([]);
  const [email, setemail] = useState<string[]>([]);
  const [pdf_content, setpdf_content] = useState<string[]>([]);
  const [jd, setjd] = useState<string[]>([]);
  const [events, setEvents] = useState<EventType[]>([]);
  const [draft, setdraft] = useState<string[]>([]);
  // const [emaildraftList, setemaildraftList] = useState<EmailDraftInfo[]>([]);
  const [currentJobId, setCurrentJobId] = useState<string>("");

  // useEffects
  useEffect(() => {
    let intervalId: number;
    console.log("currentJobId", currentJobId);
    const fetchJobStatuspdf = async () => {
      try {
        console.log("calling fetchJobStatus");
        const response = await axios.get<{
          status: string;
          result: string[];
          events: EventType[];
        }>(`/api/crew/${currentJobId}`);
        const { status, events: fetchedEvents, result } = response.data;

        console.log("status update", response.data);

        setEvents(fetchedEvents);
        if (result) {
          console.log("setting job result", result);
          setdraft(result || []);
        }

        if (status === "COMPLETE" || status === "ERROR") {
          if (intervalId) {
            clearInterval(intervalId);
          }
          setRunning(false);
          toast.success(`Job ${status.toLowerCase()}.`);
        }
      } catch (error) {
        if (intervalId) {
          clearInterval(intervalId);
        }
        setRunning(false);
        toast.error("Failed to get job status.");
        console.error(error);
      }
    };

    if (currentJobId !== "") {
      intervalId = setInterval(fetchJobStatuspdf, 1000) as unknown as number;
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [currentJobId]);

  const startpdfJob = async () => {
    // Clear previous job data
    setEvents([]);
    setdraft();
    setRunning(true);

    try {
      const response = await axios.post<{ job_id: string }>(
        "/api/crewpdf",
        {
          first_name,
          last_name,
          email,
          pdf_content,
          jd
        }
      );

      toast.success("Job started");

      console.log("jobId", response.data.job_id);
      setCurrentJobId(response.data.job_id);
    } catch (error) {
      toast.error("Failed to start job");
      console.error(error);
      setCurrentJobId("");
    }
  };
  const startJobHR = async () => {
    // Clear previous job data
    setEvents([]);
    setdraft();
    setRunning(true);

    try {
      const response = await axios.post<{ job_id: string }>(
        "/api/crewHR",
        {
          pdf_content,
          jd
        }
      );

      toast.success("Job started");

      console.log("jobId", response.data.job_id);
      setCurrentJobId(response.data.job_id);
    } catch (error) {
      toast.error("Failed to start job");
      console.error(error);
      setCurrentJobId("");
    }
  };

  return {
    running,
    events,
    setEvents,
    currentJobId,
    setCurrentJobId,
    startpdfJob,
    startJobHR,
    jd, setjd,
    pdf_content, setpdf_content,
    email, setemail,
    last_name, setlast_name,
    first_name, setfirst_name,
    draft, setdraft
    // emaildraftList, setemaildraftList,
  };
};
