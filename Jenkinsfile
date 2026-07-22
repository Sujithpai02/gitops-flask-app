pipeline {

    agent any

    environment {
        IMAGE_NAME = "sujith0227/gitops-flask-app"
        IMAGE_TAG = "${BUILD_NUMBER}"
        SCANNER_HOME = tool 'SonarScanner'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest -v
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
                    sh """
                        ${SCANNER_HOME}/bin/sonar-scanner \
                        -Dsonar.host.url=http://sonarqube:9000 \
                        -Dsonar.token=$SONAR_TOKEN \
                        -Dsonar.projectKey=gitops-flask-app \
                        -Dsonar.sources=. \
                        -Dsonar.python.version=3 \
                        -X
                    """
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t $IMAGE_NAME:$IMAGE_TAG .
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push $IMAGE_NAME:$IMAGE_TAG
                    '''
                }
            }
        }

        stage('Update GitOps Repository') {
            steps {
                sshagent(credentials: ['github-ssh']) {
                    sh '''
                        rm -rf gitops-flask-manifests

                        git clone git@github.com:Sujithpai02/gitops-flask-manifests.git

                        cd gitops-flask-manifests

                        git config user.name "Jenkins CI"
                        git config user.email "jenkins@local"

                        sed -i "s|image: .*|image: $IMAGE_NAME:$IMAGE_TAG|g" flask/deployment.yaml

                        git add flask/deployment.yaml

                        git commit -m "Update image to $IMAGE_TAG" || true

                        git push origin main
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully!"
        }

        failure {
            echo "Pipeline failed!"
        }
    }
}
