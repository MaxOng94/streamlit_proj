## Prerequisites

- Anaconda installed
- Python 3.x
- Required Python packages (install with `pip install -r requirements.txt`):
  - `pandas`
  - `numpy`
  - `scikit-learn`
  -

## Installation

1. Navigate to the project repository:

   ```bash
   cd streamlit_proj
   ```

2. Run the cmd below to create and install requirements packages:

   ```bash
   conda env create --name streamlit_sia --file conda.yml
   conda activate streamlit_sia
   ```

3. Usage

   Run the training pipeline as follows:

   ```bash
    streamlit run app.py
   ```

# Description

<h4 >
      In this assessment, instead of building a streamlit app from scratch, I decided to extend an existing implementation, <a href= 'https://blog.streamlit.io/chat2vis-ai-driven-visualisations-with-streamlit-and-natural-language/' > Chat2vis.</a><br>
      Chat2vis generates data visualization via natural language using LLMs such as GPT, Llama etc.
      <br><br> I've implemented these additional features :<br>
         <ol>
            <li>Changed visualization to plotly for more interactivity.
               <ul>
                     <li>Original chat2vis uses matplotlib with very limited interactivity.</li>
                     <li>With plotly, users can zoom, pan, select data points, download visualization etc.</li>
               </ul>
            </li>
            <br><li>
               Allow user to edit code generated from LLM.
               <ul>
                     <li>Users have the option to view the code output from LLM.</li>
                     <li>If user is unhappy with the generated plot, they can modify the existing code generated and execute their own code.</li>
               </ul>
            </li>
         </ol> 
</h4>


# Docker
This section contains instructions for building and running the Docker image for this project.

Build the Docker Image
To build the Docker image, run the following command from the root directory of your project:

`docker build . -t <your-image-name>`


This will create a Docker image using the instructions in the Dockerfile. Replace 
<your-image-name>
 with the name you want to give your image.

Run the Docker Container
To run a container from your built image, run:

`docker run -p <host-port>:<container-port> <your-image-name>`

This will run your image in a container, exposing the container port to the host port specified.

For example:
`docker run -p 8000:80 my-image`


Run docker with interactive bash shell to test or debug: 


`docker run -p 8000:80 -it --rm <your-image-name> /bin/bash
`

## Future work

1. Build a dashboard instead of a single visualization on streamlit
2. Refactor code at the backend

## Update

1. Created dockerfile to containerize application

### Bug fix

1. Prevent API calls when there is no user input



