pipeline {
    agent any

    stages {
        stage("hello") {
            steps {
                echo "hello"
            }
        }
        stage("cmv_gateway") {
            when {
                branch "cmv_gateway"
            }
            steps {
                sh '''
                    echo "working on API Gateway..."
                '''
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