"use client";

import { EventLog } from "@/components/EventLog";
import { EmailLog } from "@/components/EmailLog";
import axios from "axios";
import InputSection from "@/components/InputSection";
import { useCrewJob } from "@/hooks/useCrewJob";
import { FileState, MultiFileDropzone } from "@/components/FileUploader";
import { useState } from "react";
import { useEdgeStore } from '@/lib/edgestore';
import Link from "@/node_modules/next/link";

export default function Home() {
  // Hooks
  const crewJob = useCrewJob();
  const [fileStates, setFileStates] = useState<FileState[]>([]);
  const { edgestore } = useEdgeStore();
  const [urls, setUrls] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  

  function updateFileProgress(key: string, progress: FileState['progress']) {
    setFileStates((fileStates) => {
      const newFileStates = structuredClone(fileStates);
      const fileState = newFileStates.find(
        (fileState) => fileState.key === key,
      );
      if (fileState) {
        fileState.progress = progress;
      }
      return newFileStates;
    });
  }
  const handleFileAdded = async (addedFiles) => {
    setFileStates([...fileStates, ...addedFiles]);
    await Promise.all(
      addedFiles.map(async (addedFileState) => {
        try {
          const res = await edgestore.myPublicFiles.upload({
            file: addedFileState.file,
            onProgressChange: async (progress) => {
              updateFileProgress(addedFileState.key, progress);
              if (progress === 100) {
                // wait 1 second to set it to complete
                // so that the user can see the progress bar at 100%
                await new Promise((resolve) => setTimeout(resolve, 1000));
                updateFileProgress(addedFileState.key, 'COMPLETE');
              }
            },
          });
          extractText(res.url)
          setUrls([...urls, res.url]);
          console.log(res);
        } catch (err) {
          updateFileProgress(addedFileState.key, 'ERROR');
        }
      }),
    )}


  const extractText = async (url) => {
    setIsLoading(true);

    try {
      const response = await axios.post('/api/extract-text', { url });
      crewJob.setpdf_content(response.data.text);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };


  return (
    <div className="bg-white min-h-screen text-black">
      <div className="flex">
        <div className="w-1/2 p-4">
          
          <InputSection
            title="First Name"
            placeholder="First Name"
            data={crewJob.first_name}
            setData={crewJob.setfirst_name}
          />
          <InputSection
            title="Last Name"
            placeholder="Last Name"
            data={crewJob.last_name}
            setData={crewJob.setlast_name}
          />
          <InputSection
            title="Email"
            placeholder="Email"
            data={crewJob.email}
            setData={crewJob.setemail}
          />
          <MultiFileDropzone
                value={fileStates}
                dropzoneOptions={{
                  maxSize: 1024 * 1024 * 4
                }}
                onChange={(files) => {
                  setFileStates(files);
                }}
                onFilesAdded={handleFileAdded}
              />
          <InputSection
            title="JD"
            placeholder="JD"
            data={crewJob.jd}
            setData={crewJob.setjd}
          />
        </div>
        <div className="w-1/2 p-4 flex flex-col">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Output</h2>
            
            <button
              onClick={() => crewJob.startpdfJob()}
              className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded text-sm"
              disabled={crewJob.running}
            >
              {crewJob.running ? "Running..." : "Draft email"}
            </button>
            <button
              onClick={() => crewJob.startJobHR()}
              className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded text-sm"
              disabled={crewJob.running}
            >
              {crewJob.running ? "Running..." : "Find Match"}
            </button>
          </div>
          <EmailLog email={crewJob.draft} />
          <EventLog events={crewJob.events} />
        </div>
      </div>
    </div>
  );
}