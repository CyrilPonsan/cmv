pipeline {
    agent any
    
    tools {
        nodejs 'nodejs'
    }
    
    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        IMAGE_GATEWAY = "firizgoude/cmv_gateway"
        IMAGE_TAG = "gateway-${env.BUILD_NUMBER}"
        NPM_CACHE_DIR = "tmp/npm-cache"
        BRANCH_NAME = "${env.GIT_BRANCH.split('/').last()}"
    }
    
    stages {
        stage("Checkout") {
            steps {
                checkout scm
                script {
                    echo "Current branch is ${BRANCH_NAME}"
                }
            }
        }
        
        stage("API Gateway Operations") {
            when {
                expression { BRANCH_NAME == 'cmv_gateway' }
            }
            stages {
                stage('Install Dependencies') {
                    steps {
                        dir('cmv_gateway/cmv_front') {
                            sh """
                            mkdir -p ${NPM_CACHE_DIR}
                            npm config set cache ${NPM_CACHE_DIR}
                            npm ci --prefer-offline
                            """
                        }
                    }
                }
                stage('Run Tests') {
                    steps {
                        dir('cmv_gateway/cmv_front') {
                            sh 'npm run test:unit'
                        }
                    }
                }
                stage('Build Image') {
                    steps {
                        dir('cmv_gateway') {
                            script {
                                sh "echo 'Starting Docker build...'"
                                sh "docker --version"
                                sh "pwd"
                                sh "ls -la"
                                def dockerImage = docker.build("${IMAGE_GATEWAY}:${IMAGE_TAG}", "-f Dockerfile .")
                                sh "echo 'Docker build completed.'"
                            }
                        }
                    }
                }
                stage('Push to DockerHub') {
                    steps {
                        sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
                        sh "docker push ${IMAGE_GATEWAY}:${IMAGE_TAG}"
                    }
                }
            }
        }
        
        stage("cmv_patients") {
            when {
                expression { BRANCH_NAME == 'cmv_patients' }
            }
            steps {
                sh '''
                    echo "working on API Patients..."
                '''
            }
        }
    }
    
    post {
        always {
            sh 'docker logout'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Please check the logs.'
        }
    }
}