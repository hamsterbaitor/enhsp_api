from typing import Annotated

from fastapi import FastAPI, File, UploadFile, HTTPException

import uuid, subprocess, pathlib, logging

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.INFO)

app = FastAPI()


async def generate_mugs_output(domain_pddl_fn, problem_pddl_fn):
    command = ['java', '-cp', '/enhsp-xaip/out/:/enhsp-xaip/jar_dependencies/*', 'GoalConflictAnalysis', domain_pddl_fn, problem_pddl_fn]
    
    logger.info("Command: " + str(command))
    
    output = None
    result = subprocess.run(command, capture_output=True,  text=True, cwd="/enhsp-xaip/")
    
    output = result.stdout.strip()
    
    return output
    
@app.post("/mugs_from_pddl/")
async def uploadfile(domain_pddl: str, problem_pddl: str, files: list[UploadFile]):
    logger.info('Number of files received: ' + str(len(files)))
    if len(files) != 2:
        raise HTTPException(status_code=400, detail="Request must have exactly two files attached.")
    # Simple error check to make sure provided domain and problem filenames are in uploaded files.
    if not(((domain_pddl == files[0].filename) or (domain_pddl == files[1].filename)) and ((problem_pddl == files[0].filename) or (problem_pddl == files[1].filename))):
        raise HTTPException(status_code=400, detail="Malformed request - filenames of uploade files must match the specified domain and problem pddls")
    
    logger.debug('Current domain pddl: ' + domain_pddl)
    logger.debug('Current problem pddl: ' + problem_pddl)
    domain_pddl_fn = "/tmp/" + domain_pddl
    problem_pddl_fn = "/tmp/" + problem_pddl
        
    try: 
        for file in files:
            if(file.filename == domain_pddl):
                with open(domain_pddl_fn, "wb") as f:
                    f.write(file.file.read())
            else:
                with open(problem_pddl_fn, "wb") as f:
                    f.write(file.file.read())
        
        output = await generate_mugs_output(domain_pddl_fn, problem_pddl_fn)
        return output
    
    except Exception as e:
        return {"message": e.args}