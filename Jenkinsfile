pipeline {
    agent any

    envrionment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        IMAGE_GATEWAY = "firizgoude-dockerhub/cmv_gateway"
        IMAGE_TAG = "gateway-${env.BUILD_NUMBER}"
        NPM_CACHE_DIR = "tmp/npm-cache"
    }

    stages {
        stage("Hello") {
            steps {
                echo "hello"
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage("API Gateway") {
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
                        script {
                            docker.build("${IMAGE_NAME}:${IMAGE_TAG}")
                        }
                    }
                }
                stage('Push to DockerHub') {
                    steps {
                        sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
                        sh "docker push ${IMAGE_NAME}:${IMAGE_TAG}"
                    }
                }
            }
        }





        stage("cmv_patients") {
            when {
                branch "cmv_patients"
            }
            steps {
                sh '''
                    echo "working on API Patients..."
                '''
            }
        }
    }
}